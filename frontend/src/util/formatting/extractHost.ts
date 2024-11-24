export function extractHost(url: string): string {
   // Extracts the host after the protocol, but before the first slash (Due to heroku random subdomain)
   const host = url.split('/')[2];
   const name = host.split('.')[0];
   const appName = name.split('-').slice(0, -1).join('-');
   return appName;
}