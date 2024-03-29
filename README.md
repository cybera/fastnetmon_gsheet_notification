# FastNetMon Event Notifications for Google Spreadsheets

## Installation

1. Place the notify_json_v2.py file in your `/usr/local/bin/` folder

2. Set it as executable

```shell
sudo chmod +x /usr/local/bin/notify_json_v2.py
```

3. In FastNetMon set the following:

```
sudo fcli set main notify_script_enabled enable
sudo fcli set main notify_script_format json
sudo fcli set main notify_script_path /usr/local/bin/notify_json_v2.py
sudo fcli commit
```

## Google API Instructions

4. Enable the Google Sheets API and set your credentials.json file in the config. The initial setup will require you to create a Google project and enable the Google Drive  and Sheets API on it. To do this, please see these instructions adopted from df2gspread:

To allow a script to use Google Drive API we need to authenticate our
self towards Google. To do so, we need to create a project, describing
the tool and generate credentials. Please use your web browser and go to https://console.developers.google.com and :

-  Choose **Create Project** in popup menu on the top.
-  A dialog box appears, so give your project a name and click on
   **Create** button.
-  On the left-side menu click on **API Manager**.
-  A table of available APIs is shown. Switch **Drive API** and click on
   **Enable API** button. Do the same for **Sheets API**. Other APIs might
   be switched off, for our purpose.
-  On the left-side menu click on **Credentials**.
-  In section **OAuth consent screen** select your email address and
   give your product a name. Then click on **Save** button.
-  In section **Credentials** click on **Add credentials** and switch
   **OAuth client ID** (if you want to use your own account or enable
   the use of multiple accounts) or **Service account key** (if you prefer
   to have a service account interacting with spreadsheets).

-  If you select **OAuth client ID**:
   -  Select **Application type** item as **Other** and give it a name.
   -  Click on **Create** button.
   -  Click on **Download JSON** icon on the right side of created
      **OAuth client IDs** and store the downloaded file on your file system.

-  If you select **Service account key**
   -  Click on **Service account** dropdown and select **New service account**
   -  Give it a **Service account name** and ignore the **Role** dropdown
      (unless you know you need this for something else, it's not necessary for
      working with spreadsheets)
   -  Note the **Service account ID** as you might need to give that user
      permission to interact with your spreadsheets
   -  Leave **Key type** as **JSON**
   -  Click **Create** and store the downloaded file on your file system.

5. Rename the file to `fnm_google_notify.json` and save it to `~/.fnm_google_notify.json`.

6. Open `~/.fnm_google_notify.json` and add an additional field of the URL to the
spreadsheet to save the data to:

```
"sheet_url": "https://docs.google.com/spreadsheets/d.....",
```

6. Test the script with the following syntax:

```
cat ban.json | python notify_json_v2.py ban 192.168.1.1
```
