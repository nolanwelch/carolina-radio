import Cookies from "js-cookie";
import Song from "./types/Song";
import axios, { AxiosResponse } from 'axios';
import NowPlayingSong from "./types/NowPlayingSong";

const NetworkService = {
  getNowPlaying: async function(): Promise<NowPlayingSong> {
    const response = await axios.get<NowPlayingSong>(process.env.REACT_APP_API_URL + "/api/playback/playing");
    return response.data;
  },
  getQueue: async function(): Promise<Array<Song>> {
    const response = await axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/api/playback/queue");
    return response.data;
  },
  requestSong: function(song: Song) {
    return axios.post<Array<Song>>(process.env.REACT_APP_API_URL + "/api/playback/request", {songId: song.songId},{
      withCredentials: true,
    })
  },
  getSearchSong: async function(query: string): Promise<Array<Song>> {
    return axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/api/playback/search", {
      params: {
        query: query
      },
      withCredentials: true,
    }).then((response: AxiosResponse<Song[], any>) => response.data)
  },
}

export default NetworkService;