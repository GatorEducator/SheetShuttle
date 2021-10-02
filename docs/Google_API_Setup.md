# Steps

[Helpful Video](https://www.youtube.com/watch?v=4ssigWmExak)

- Create a project for google API from [cloud console](https://console.cloud.google.com/)
  - Fill out all needed info for the project
- Enable Google sheets API
  - Click on `Go to API's overview`
  - Click on `Enable APIs and Services`
  - Look up and click on Google Sheets API
  - Click Enable
- Create credentials for service accounts with the needed access
  - Go to console home screen
  - Expand the left menu to `APIs and Services`, click on  `Credentials`
  - Click `Create Credentials` and then on `Service Account`
  - Fill out the required info
  - Once Completed, go to the `keys` section and create a new key of JSON type
  - Json file will get downloaded
- Manually share the google sheet with the service account email (annoying step)
- Range from where data will be read must be specified in the program (unless
  there is a way to automatically detect where the data ends)