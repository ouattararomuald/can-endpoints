# can-endpoints

Simple API for the Africa Cup of Nation.

See [Google Cloud Endpoints][1].

## RSS feed Source
[match en direct](http://www.matchendirect.fr/)

## Dependencies
[Feedparser][2]

## Run Locally
1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
See the README file for directions. You'll need Python 2.7 installed too.

2. Clone this repo with

   ```
   git clone https://github.com/ouattararomuald/can-endpoints.git
   ```
3. Run the application locally with

   ```
   cd can-endpoints
   dev_appserver.py .
   ```
4. Test your Endpoints by visiting the Google APIs Explorer (by default [http://localhost:8080/_ah/api/explorer](http://localhost:8080/_ah/api/explorer))

## Deploy
To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create an app.
2. Replace `<your-app-id>` in `app.yaml` with the app id from the previous step.
4. Invoke the upload script as follows (**Source**: [Testing and Deploying an API Backend][3]):

   ```
   sdk-install-directory/appcfg.py update app-directory
   ```
where `sdk-install-directory` is the directory where you installed the App Engine SDK, and `app-directory` is the directory containing your backend code. (As shown, `app-directory` is a subdirectory of the current directory; you could alternatively specify a full path.)

Full instructions for deploying are provided in the topic [Uploading, Downloading, and Managing a Python App][4].

After you deploy, you can use the API Explorer to experiment with your API without using a client app by visiting:
   ```
   https://your_app_id.appspot.com/_ah/api/explorer
   ```

[1]: https://cloud.google.com/appengine/docs/python/endpoints/
[2]: https://github.com/kurtmckee/feedparser
[3]: https://cloud.google.com/appengine/docs/python/endpoints/test_deploy
[4]: https://cloud.google.com/appengine/docs/python/tools/uploadinganapp

## Contributing
Please see the [contributing guide](CONTRIB.md)

## Licence
```
Copyright 2015 Ouattara Gninlikpoho Romuald

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
