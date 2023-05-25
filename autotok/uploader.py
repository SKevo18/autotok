import typing as t

import pickle

from pathlib import Path
from warnings import warn

from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from autotok import MODULE_ROOT


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

CLIENT_SECRET_PATH = MODULE_ROOT.parent / 'client_secret.json'
TOKEN_PICKLE_PATH = MODULE_ROOT.parent / 'token.pickle'



def authenticate() -> Resource:
    creds: t.Optional[Credentials] = None

    if TOKEN_PICKLE_PATH.exists():
        with TOKEN_PICKLE_PATH.open('rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES, redirect_uri="http://localhost:24053/")
            creds = flow.run_local_server(port=24053)

        with TOKEN_PICKLE_PATH.open('wb') as token:
            pickle.dump(creds, token)


    return build('youtube', 'v3', credentials=creds)



def upload_to_youtube(video_path: Path, title: str, description: t.Text, category_id: int, tags: list, playlist_id: t.Optional[str]=None):
    youtube = authenticate()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": 'public'
        }
    }
  

    insert_request = youtube.videos().insert( # type: ignore
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )


    response = None

    while response is None:
        _, response = insert_request.next_chunk()


    if response is not None:
        if video_id := response.get('id', None):
            if playlist_id is not None:
                added_playlist = youtube.playlistItems().insert( # type: ignore
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id, 
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()

                print(f"Added video to playlist `{added_playlist['id']}`")

            return video_id

        else:
            warn(f"The upload failed with an unexpected response: {response}")



if __name__ == '__main__':
    authenticate()
