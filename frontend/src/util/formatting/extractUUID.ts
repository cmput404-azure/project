export function extractUUID(fqid: string): string {
    const uuid = fqid.split('/').pop();
    return uuid;
}