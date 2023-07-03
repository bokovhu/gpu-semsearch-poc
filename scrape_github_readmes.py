from semsearchdatasets import GitHubReadmeScraper, GitHubReadmeReferenceScraper

if __name__ == "__main__":
    scraper = GitHubReadmeScraper(
        repos=[
            "sindresorhus/awesome",
            "Awesome-Windows/Awesome",
            "vinta/awesome-python",
            "avelino/awesome-go",
            "vuejs/awesome-vue",
            "akullpp/awesome-java",
            "enaqx/awesome-react",
            "fffaraz/awesome-cpp",
            "josephmisiti/awesome-machine-learning",
            "jaywcjlove/awesome-mac",
            "docker/awesome-compose",
            "Solido/awesome-flutter",
            "vsouza/awesome-ios",
        ],
        output_directory="./input.github",
    )
    # scraped_repos = scraper.scrape()

    reference_scraper = GitHubReadmeReferenceScraper(
        input_readmes_directory="./input.github-referenced-readmes",
        output_directory="./input.github-references",
    )
    scraped_urls = reference_scraper.scrape()

    github_repository_urls = [
        u for u in scraped_urls if u.startswith("https://github.com/")
    ]
    github_repository_urls = list(set(github_repository_urls))

    referenced_github_repos = [
        u.replace("https://github.com/", "") for u in github_repository_urls
    ]
    referenced_github_repos = [r for r in referenced_github_repos if r.count("/") == 1]

    print(f"Found {len(referenced_github_repos)} referenced GitHub repositories")

    scraper = GitHubReadmeScraper(
        repos=referenced_github_repos,
        output_directory="./input.github-referenced-readmes-2",
    )
    scraped_repos = scraper.scrape()
