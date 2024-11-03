export default interface Song {
    songId: string,
    title: string;
    artists: Array<string>;
    album: string;
    coverUrl: string;
    lengthMs: number;
    requestCount: number;
}