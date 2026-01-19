import axios from 'axios';

const api = axios.create({
    baseURL: '/api/repo', // Proxied by Vite to http://localhost:8000/repo
});

export const getRepoTree = async (owner, repo) => {
    const response = await api.get(`/tree?owner=${owner}&repo=${repo}`);
    return response.data;
};

export const getFileContent = async (owner, repo, path) => {
    const response = await api.get(`/file?owner=${owner}&repo=${repo}&path=${path}`);
    return response.data;
};

export const analyzeFile = async (owner, repo, path) => {
    const response = await api.get(`/analyze-file?owner=${owner}&repo=${repo}&path=${path}`);
    return response.data;
}

export const getReport = async (owner, repo) => {
    const response = await api.get(`/report?owner=${owner}&repo=${repo}`);
    return response.data;
}

export const getRoadmap = async (owner, repo) => {
    const response = await api.get(`/roadmap?owner=${owner}&repo=${repo}`);
    return response.data;
}

export const getContributionGuide = async (owner, repo) => {
    const response = await api.get(`/contribution-guide?owner=${owner}&repo=${repo}`);
    return response.data;
}

export default api;
