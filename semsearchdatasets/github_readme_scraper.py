import requests
import os
import re
import asyncio


class GitHubReadmeScraper:
    def __init__(self, repos=[], output_directory="./input") -> None:
        self.repos = repos
        self.output_directory = output_directory

    async def scrape_one(self, repo_name, sem):
        async with sem:
            print(f"Scraping {repo_name}...")
            output_file_name = repo_name.replace("/", "_") + ".md"
            output_file_path = f"{self.output_directory}/{output_file_name}"

            if os.path.exists(output_file_path):
                print(f"Skipping {repo_name} because {output_file_name} already exists")
                return open(output_file_path, "r", encoding="utf-8").read()

            repo_url = f"https://raw.githubusercontent.com/{repo_name}/master/README.md"
            response = await asyncio.get_event_loop().run_in_executor(
                None, requests.get, repo_url
            )
            if response.status_code == 200:
                readme_content = response.text
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(readme_content)
                return readme_content
            else:
                print(f"Could not scrape {repo_name} because {response.status_code}")
                return None

    async def scrape_async(self, batch):
        all_readmes = {}

        scrape_tasks = []
        sem = asyncio.Semaphore(16)
        for repo_name in batch:
            scrape_tasks.append(self.scrape_one(repo_name, sem))

        for scrape_task in asyncio.as_completed(scrape_tasks):
            readme_content = await scrape_task
            if readme_content:
                all_readmes[repo_name] = readme_content

        return all_readmes

    def scrape(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        return asyncio.run(self.scrape_async(self.repos))


def extract_urls(content):
    url_regex = r"\[.*?\]\((http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)"

    urls = re.findall(url_regex, content)

    return [
        u
        for u in urls
        if "[" not in u and "(" not in u and ")" not in u and "]" not in u
    ]


class GitHubReadmeReferenceScraper:
    def __init__(
        self,
        input_readmes_directory="./input.github",
        output_directory="./input.github-references",
    ) -> None:
        self.input_readmes_directory = input_readmes_directory
        self.output_directory = output_directory

    def scrape(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        all_urls = []

        for root, dirs, files in os.walk(self.input_readmes_directory):
            for file in files:
                if file.endswith(".md"):
                    input_file_path = os.path.join(root, file)
                    output_file_path = os.path.join(self.output_directory, file)

                    if os.path.exists(output_file_path):
                        print(
                            f"Skipping {input_file_path} because {output_file_path} already exists"
                        )
                        with open(output_file_path, "r", encoding="utf-8") as f:
                            urls = f.read().split("\n")
                            all_urls.extend(urls)
                        continue

                    with open(input_file_path, "r", encoding="utf-8") as f:
                        readme_content = f.read()

                    urls = extract_urls(readme_content)

                    with open(output_file_path, "w", encoding="utf-8") as f:
                        for url in urls:
                            f.write(f"{url}\n")

                    all_urls.extend(urls)

                    print(f"Scraped {len(urls)} urls from {input_file_path}")

        return all_urls
