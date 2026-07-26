import { apiClient } from './client';
import type {
    PushRequest,
    PushResponse,
    IndexInfoResponse,
    SearchRequest,
    SearchResponse,
    AnswerResponse,
} from './types';

export const pushToIndex = async (
    projectId: number,
    request: PushRequest
): Promise<PushResponse> => {
    const response = await apiClient.post<PushResponse>(
        `/nlp/index/push/${projectId}`,
        request
    );
    return response.data;
};

export const getIndexInfo = async (
    projectId: number
): Promise<IndexInfoResponse> => {
    const response = await apiClient.get<IndexInfoResponse>(
        `/nlp/index/info/${projectId}`
    );
    return response.data;
};

export const searchIndex = async (
    projectId: number,
    request: SearchRequest
): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>(
        `/nlp/index/search/${projectId}`,
        request
    );
    return response.data;
};

export const getAnswer = async (
    projectId: number,
    request: SearchRequest
): Promise<AnswerResponse> => {
    const response = await apiClient.post<AnswerResponse>(
        `/nlp/index/answer/${projectId}`,
        request
    );
    return response.data;
};
