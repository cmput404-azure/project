// Return string or number of the Post's visibility
export function normalizeVisibility (visibility: number | string, toString: boolean = false): string | number {
    if (visibility === 1 || visibility === "PUBLIC") {
        return toString ? "PUBLIC" : 1;
    } else if (visibility === 2 || visibility === "FRIENDS") {
        return toString ? "FRIENDS" : 2;
    } else if (visibility === 3 || visibility === "UNLISTED") {
        return toString ? "UNLISTED" : 3;
    } else if (visibility === 4 || visibility === "DELETED") {
        return toString ? "DELETED" : 4;
    }
}