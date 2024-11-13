import { api } from "./config";

interface ConfigResponse {
    require_approval: boolean;
}

interface Node {
    host: string,
    username: string,
    password: string,
    is_authenticated: boolean
}

class SettingService {
    /**
     * Fetches the current value of the registration approval toggle from the server.
     * @returns current status of `require_approval`. Returns `false` if an error occurs.
     */
    public async getToggleValue() {
        try {
            const request = await api.get<ConfigResponse>('/api/config/')
            return request.data.require_approval;
        } catch (err) {
            console.error("Error fetching registration toggle value: ", err);
            return false;
        }
    }

    /**
     * Updates the registration approval toggle status on the server.
     * @param {boolean} newStatus - The new value to set for `require_approval`.
     * @returns updated configuration response if successful, or `undefined` if an error occurs.
     */
    public async updateToggle(newStatus: boolean) {
        try {
            const request = await api.post<ConfigResponse>('/api/config/', {
                require_approval: newStatus
            });
            return request.data;
        } catch (err) {
            console.error("Error fetching registration toggle value: ", err);
        }
    }

    public async getNodeList() {
        try {
            const request = await api.get<Node[]>('/api/nodes/')
            return request.data
        } catch (err) {
            console.error("Error fetching list of nodes: ", err);
            return [];
        }
    }
}

const setting = new SettingService();
export default setting;