export function extractPostUUID(postFQID: string): string {
    const uuid = postFQID.split('/').pop();
    return uuid;
}