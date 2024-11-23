export function extractUUID(fqid: string): string {
    const sanitizedFqid = fqid.replace(/\/+$/, ''); // Remove trailing slash for consistency
    const uuid = sanitizedFqid.split('/').pop();
    return uuid;
}