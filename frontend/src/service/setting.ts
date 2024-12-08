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
            const request = await api.put<ConfigResponse>('/api/config/', {
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

    public async addNode(username: string, password: string, fullUrl: string) {
        try {
            const response = await api.post('/api/nodes/add/', {
                username: username,
                password: password,
                host: fullUrl,
            });
            return response.data; // success message

        } catch (error) {
            if (error.response) {
                return error.response.data; // informational error message from the backend
            }
            throw new Error('An unexpected error occurred');
        }
    }

    public async updateNode(username: string, password: string, fullUrl: string, status: boolean, oldHost: string) {
        try {
            const response = await api.put('/api/nodes/update/', {
                username: username,
                password: password,
                host: fullUrl,
                isAuth: status,
                oldHost: oldHost
            });
            return response.data;

        } catch (error) {
            if (error.response) {
                return error.response.data;
            }
            throw new Error('An unexpected error occurred');
        }
    }

    public async deleteNode(username: string) {
        try {
            const response = await api.delete(`/api/nodes/delete/?username=${username}`);
            if (response.status === 200) {
              console.log('Node deleted successfully');
              return response.data;
            } else {
              throw new Error('Failed to delete node');
            }
          } catch (error) {
            console.error('Error deleting node:', error);
            throw error;
          }
    }
}

const setting = new SettingService();
export default setting;