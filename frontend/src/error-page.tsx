import { useRouteError } from "react-router-dom";

export default function ErrorPage() {
  const error: any = {
   'status': 404,
   'statusText': 'Not Found',
   'message': 'The requested resource was not found.'
  }
  console.error(error);

  return (
    <div id="error-page">
      <h1>Azure encountered an error.</h1>
      <p>{error.status}</p>
      <p>
        <i>{error.statusText || error.message}</i>
      </p>
    </div>
  );
}