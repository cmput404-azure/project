// A function to normalize a given url to it's base form (includes port if it exists)
export function normalizeURL(url: string) {
    const parsedUrl = new URL(url);
    return `${parsedUrl.protocol}//${parsedUrl.host}`; // the host contains the port (if it exists)
}
