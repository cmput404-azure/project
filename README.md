[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)
CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

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
    - `lib` folder that comtains non-React code
        - `libName` folder of a library of helper functions
            - `libName.ts` file of helper function
    - `App.tsx` contains the main React component
    - `index.tsx`  entry point for the React app
    - `App.module.scss` contains the CSS for the React app
    - `index.css` contains the global CSS
    - `.env` contains the environment variables (not included in the repo, make one locally)

## Setup
Since the backend and frontend are separated in a monorepo, both need to be setup differently.
You must `cd` into each directory separately. Two terminals are required to run both servers, unless you are using something like `tmux`.

### Frontend
1. `cd` into the frontend directory
2. Run `npm i` to install the dependencies
3. Create a `.env` file in the root directory of the frontend directory
- The `.env` file should contain the following variables:
    ```
    REACT_APP_SOMETHING = 'something'
    ```
4. Run `npm start` to start the development server


### Backend
1. `cd` into the backend directory
2. 

## Deployment
The common deployment method is that both the frontend and backend require its own `Procfile` for a separate Heroku dyno, they cannot be run on the same dyno.

### Frontend
Instructions here...
### Backend
Instructions here...