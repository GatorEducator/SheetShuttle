<!-- TODO: add tutorial on how to share a sheet with the service account -->
# Google API Setup

- Create a Google API project from [cloud console](https://console.cloud.google.com/)
  - Click on select project, or create new project

![new_project1](../images/new_project1.png)
![new_project2](../images/new_project2.png)
![new_project3](../images/new_project3.png)

- Enable Google Sheets API from the [API Menu](https://console.cloud.google.com/apis/dashboard)

![sheets_api1](../images/sheets_api1.png)
![sheets_api2](../images/sheets_api2.png)
![sheets_api3](../images/sheets_api3.png)
![sheets_api4](../images/sheets_api4.png)

- Create credentials for service accounts with the needed access from the
  [Sheets Overview
  page](https://console.cloud.google.com/apis/api/sheets.googleapis.com/overview)
  - click on `create credentials`

![credentials1](../images/credentials1.png)

- Fill the information as shown here

![credentials2](../images/credentials2.png)
![credentials3](../images/credentials3.png)

- Select your service account name

![credentials4](../images/credentials4.png)
![credentials5](../images/credentials5.png)

- This information can be left blank

![credentials6](../images/credentials6.png)

- Click on the newly created service account and navigate to the keys tab

![credentials7](../images/credentials7.png)

- Click on `Add Key` and select `Create new key`

![credentials8](../images/credentials8.png)

- Select JSON and click create, a json file will be downloaded in your
    `downloads` folder

![credentials9](../images/credentials9.png)
