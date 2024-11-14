import { RemoteFollowRequest } from "../models/models";
import { extractUUID } from "../util/formatting/extractUUID";
import { normalizeURL } from "../util/formatting/normalizeURL";
import { api, basicAuthApi } from "./config";

// Currently contains anything to do with remote follow requests
class RemoteService {
    private buildEncodedPath(host, id) {
        return encodeURIComponent(`${normalizeURL(host)}/api/authors/${extractUUID(id)}`);
    }

    private buildNormalPath(host, id) {
        return `${normalizeURL(host)}/api/authors/${extractUUID(id)}`;
    }
    /**
     * The remote follow request was accepted, update accordingly in our local DB.
     * @param uuid - UUID of local follower
     * @param remoteHost - Host URL of remote followee
     * @param remoteId - UUID of remote followee
     * @returns a message indicating success or failure
     */
    public async setRequestAsAccepted(uuid: string, remoteHost: string, remoteId: string) {
        try {
            const request = await api.post<{ message: string }>(
                `/api/track/${uuid}/accepted/${this.buildEncodedPath(remoteHost, remoteId)}`
            );
            return request.data.message;
        } catch (err) {
            console.error("Something went wrong: ", err);
        }
    }

    /**
     * Remote follow request has a corresponding Follow item, remote the Follow Request record
     * @param uuid - UUID of local follower
     * @param remoteHost - Host URL of remote followee
     * @param remoteId - UUID of remote followee
     * @returns a message indicating success or failure
     */
    public async deleteStaleRequest(uuid: string, remoteHost: string, remoteId: string) {
        try {
            const request = await api.delete<{ message: string }>(
                `/api/track/${uuid}/delete/${this.buildEncodedPath(remoteHost, remoteId)}`
            );
            return request.data.message;
        } catch (err) {
            console.error("Something went wrong: ", err);
        }
    }

    /**
     * Tracking if remote requests are accepted, or still pending, or perhaps rejected
     * @param uuid - UUID of local follower whose remote follow requests we want to track
     * @returns array of remote follow requests that belongs to the user with pending status = True
     */
    public async checkRequestStatus(uuid: string) {
        try {
            const response = await api.get<RemoteFollowRequest[]>(
                `/api/track/${uuid}/pending/`
            );
            return response.data;
        } catch (err) {
            console.error("Error fetching follow requests: ", err);
        }
    }

    /**
     * Tracking if remote requests are accepted, or still pending, or perhaps rejected
     * @param uuid - UUID of local follower whose remote follow requests we want to track
     * @returns array of remote follow requests that belongs to the user with pending status = True
     */
    public async trackRemoteRequest(uuid: string, requestObject: object) {
        try {
            const response = await api.post<RemoteFollowRequest[]>(
                `/api/authors/${uuid}/track/`, requestObject
            );
            return response.data;
        } catch (err) {
            console.error("Error fetching follow requests: ", err);
        }
    }

    /**
     * Check if local user is a follower or remote author on the remote node.
     * @param followeeHost - Host URL of remote followee
     * @param followeeId - UUID of the remote followee
     * @param localHost - Host URL of local user (follower)
     * @param localId - UUID of local user (follower)
     * @returns false if local user is not a follower of remote author, true otherwise.
     */
    public async checkRemoteNode(followeeHost: string, followeeId: string, localHost: string, localId: string) {
        try {

            const localFQID = encodeURIComponent(localHost + 'authors/' + localId);
            const remoteEndpoint = `${normalizeURL(followeeHost)}/api/authors/${extractUUID(followeeId)}/followers/${localFQID}`;

            const request = await basicAuthApi.get<{ "is_follower": false }>(remoteEndpoint);
            return request.data.is_follower;
        } catch (err) {
            if (err.response?.status === 404) {
                // 404 means request still pending or rejected
                return false;
            } else {
                console.error("Error checking follow request status: ", err);
                return false;
            }
            
        }
    }

        /**
         * Send a single object of type Post/FollowRequest to remote author's inbox
         * @param remoteId - the uuid of the remote user
         * @param inboxItem - the inbox item to be sent
         * @param remoteHost - the service or base url of the remote node
         * @returns a string message
        */
        public async sendItemRemotely(remoteHost: string, remoteId: string, inboxItem: object) {
            console.log(`Sending to: ${remoteId} on ${remoteHost}`)
            try {
                const inboxResponse = await basicAuthApi.post<{ message: string }>(
                    `${this.buildNormalPath(remoteHost, remoteId)}/inbox/`,
                    inboxItem
                );
                return inboxResponse.data.message;
            } catch (error) {
                console.error(`Error sending object to inbox of ${extractUUID(remoteId)}:`, error);
                return null;
            }
        }
}

const remote = new RemoteService();
export default remote;