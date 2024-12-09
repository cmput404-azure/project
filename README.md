[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)

# CMPUT404-project-socialdistribution

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

Link: https://azuredsn-889a4fb9b2bb.herokuapp.com/

Docs: https://azuredsn-889a4fb9b2bb.herokuapp.com/api/docs

### Images
![image](https://github.com/user-attachments/assets/ff4d75a5-ad67-4f48-9706-faf732635f32)
![image](https://github.com/user-attachments/assets/6b7d40d6-5646-4501-8763-b7574485489d)
![image](https://github.com/user-attachments/assets/9010b476-a3d7-4d6f-9dcd-c3fb237f8193)
![image](https://github.com/user-attachments/assets/b9843ed8-a324-461d-b950-e83ba20e17e9)
![image](https://github.com/user-attachments/assets/aa6ccabc-d7f5-4bb9-96b9-843ab4b640e6)
![image](https://github.com/user-attachments/assets/fc04571e-5fe0-4359-85d4-c74987d4a48d)
![image](https://github.com/user-attachments/assets/7cf151f1-c17b-4d4f-a8c6-95fb3afa8a81)
![image](https://github.com/user-attachments/assets/4d15ab89-75a1-4d02-8318-abf754856eff)

### Video
https://www.youtube.com/watch?v=ZJmXECT2B4o

### Fully connected groups
- Whitesmoke
- Mistyrose
- Cornflowerblue
- Darkgoldenrod

> Note: Connection with Darkgoldenrod's node is sometimes interrupted by a HTTP 429 error ("Request was throttled")

## License

MIT License

## Copyright

Khyl Nad <br />
Quin Nguyen <br />
Kyle Quach <br />
Crystal Zhang <br />
Cinguinique Erquette <br />
Nathan Wu

## Structure

### Frontend

- `src` folder contains the source code for the frontend
  - `public` folder contains the static files (logo, static assets, etc.)
  - `components` folder contains the React components
    - `ComponentName` folder contains the React component
      - `ComponentName.tsx` contains the React component
      - `ComponentName.module.scss` contains the CSS for the React component
  - `util` folder that comtains non-React code
    - `libName` folder of a library of helper functions
      - `libName.ts` file of helper function
  - `App.tsx` contains the main React component
  - `index.tsx` entry point for the React app
  - `App.module.scss` contains the CSS for the React app
  - `index.css` contains the global CSS
  - `.env` contains the environment variables (not included in the repo, make one locally)
  - `package.json` contains the dependencies and scripts
    - `package-lock.json` contains the dependencies and scripts
    - `bun.lockb` binary lockfile for Bun (if using Bun over npm)
  - `tsconfig.json` contains the TypeScript configuration

### Backend

- `server` directory is the base directory for the django project
- `azureDSN` directory is the django app containing the files for the entire backend
   - `serializers` folder contains serializer class for each model
      - `model_serializer.py` contains the serializer class
   - `utils`: folder contains the general-purpose functions or helpers that can be reused across the entire project

- to make database migrations locally, cd into the `backend` directory and run,

    > `python3 manage.py makemigrations azureDSN`

    then,

    > `python3 manage.py migrate`

- `requirements.txt` contains all the required packages to run the django project

  - if changes have been made to the requirements, run

    > `pip install -r requirements.txt`

  - if you installed new packages locally make sure to run,

    > `pip freeze >| requirements.txt`

  - after installing the new package so that it is added to the requirements.txt file. Commit this file.

## Setup

Since the backend and frontend are separated in a monorepo, both need to be setup differently.
You must `cd` into each directory separately. Two terminals are required to run both servers, unless you are using something like `tmux`.

### Frontend

1. `cd` into the frontend directory
2. Run `npm i` to install the dependencies
3. Create a `.env` file in the root directory of the frontend directory
   - The `.env` file should contain the following variables:
     ```
         REACT_APP_API_BASE_URL="http://localhost:8000" # Change this to the correct URL in prod
     ```
4. Run `npm start` to start the development server

### Backend

1. `cd` into the backend directory
2. Create a virtual environment
   - Run `python3 -m venv .venv` to create a virtual environment
   - Run `source .venv/bin/activate` to activate the virtual environment
     - if you are using VSCode you can automatically activate the venv every time by setting the interpreter to the venv python interpreter.
3. Run `pip install -r requirements.txt` to install the dependencies
4. run `python manage.py makemigrations` to make the database migrations
5. Run `python manage.py migrate` to migrate the changes to the database
6. Run `python manage.py runserver` to start the development server

## Deployment
Note: The lock files in the root directory should be up to date before deploying
  - The lock files should NOT be used for development, only for deployment

### Setup
1. Make sure the lock files in the root directory are up to date
  - If they are not, copy the lock files from the frontend and backend directories into the root directory 

### Finalize
1. Merge into prod
2. Merge prod into deployment (it should auto deploy)

### Deploy (heroku)
1. Use buildpacks nodejs and python
2. After first deploy, run migrations and create superuser
3. Config vars:
- ![image](https://github.com/user-attachments/assets/5aa90d0a-825c-4255-8839-8e86951546ca)
4. Run `python manage.py collectstatic` in backend folder if frontend does not display.

