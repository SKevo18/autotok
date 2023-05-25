# Python AutoTok

A Python CLI tool that continuously listens to a TikTok account, and if it goes online, it downloads the stream and uploads it to YouTube.

## Get started

1. Clone the GitHub repository;
2. Obtain [YouTube API v3](https://developers.google.com/youtube/registering_an_application) `client_secret.json` and place it in the cloned repository's root (use OAuth 2 and `http://localhost:24053/` as redirect URI);
3. Run `python -m autotok.uploader` to auth via your YouTube account and pickle the generated token (keep your secrets safe!);
4. Finally, run `python -m autotok listen <tiktok_account_id>` to listen for streams, download them and upload them (use `--no-upload` to not upload the downloaded stream file - you can use `python -m autotok upload --help` to upload them later);

Note: this is still a work in progress!
