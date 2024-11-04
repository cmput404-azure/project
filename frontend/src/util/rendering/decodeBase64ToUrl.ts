// Helper function to decode base64 images back to data url format
export function decodeBase64ToUrl (posts: any[]) {
    return posts.map((post) => {
      if (
        post.contentType === "image/jpeg;base64" ||
        post.contentType === "image/png;base64" ||
        post.contentType === "application/base64"
      ) {
        post.content = `data:${post.contentType},${post.content}`;
      }
      return post;
    });
};