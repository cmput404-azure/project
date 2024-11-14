// A function to normalize a given url to it's base form
export function normalizeURL(url: string) {
    const parsedUrl = new URL(url);
    return `${parsedUrl.protocol}//${parsedUrl.host}`;
}
