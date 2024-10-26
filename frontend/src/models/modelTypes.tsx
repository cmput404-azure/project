export enum InboxItemType {
    COMMENT = "comment",
    FOLLOW = "follow",
    LIKE = "like",
    POST = "post",
}

export enum ContentType {
    BASE64 = "application/base64",
    MARKDOWN = "text/markdown",
    PLAIN = "text/plain",
}

export enum VisibilityChoices {
    PUBLIC = "PUBLIC",
    FRIENDS = "FRIENDS",
    UNLISTED = "UNLISTED",
  }
  
  // Utility function to map visibility to a number
  export const getVisibilityNumber = (visibility: VisibilityChoices): number => {
    switch (visibility) {
      case VisibilityChoices.PUBLIC:
        return 1;
      case VisibilityChoices.FRIENDS:
        return 2;
      case VisibilityChoices.UNLISTED:
        return 3;
      default:
        return 4; // This is the deleted case
    }
  };