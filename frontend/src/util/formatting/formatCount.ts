export function formatCount(count: number): string {
    if (count < 1000) {
        return count.toString();
    } else if (count >= 1000 && count < 1000000) {
        return (count / 1000).toFixed(1) + 'K'; // For thousands
    } else if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M'; // For millions
    }

    return '';
}