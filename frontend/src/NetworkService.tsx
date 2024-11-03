import Cookies from "js-cookie";
import Song from "./types/Song";
import axios, { AxiosResponse } from 'axios';
import NowPlayingSong from "./types/NowPlayingSong";

const NetworkService = {
  getNowPlaying: function(): Promise<NowPlayingSong> {
    return axios.get<NowPlayingSong>(process.env.REACT_APP_API_URL + "/now_playing").then((response: AxiosResponse<NowPlayingSong, any>) => response.data)
  },
  getQueue: function(): Promise<Array<Song>> {
    return axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/queue").then((response: AxiosResponse<Song[], any>) => response.data)
  },
  getRequestedSongs: function(): Promise<Array<Song>> {
    return axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/request", {
      withCredentials: true,
    }).then((response: AxiosResponse<Song[], any>) => response.data)
  },
  requestSong: function(song: Song) {
    return axios.post<Array<Song>>(process.env.REACT_APP_API_URL + "/request", {id: song.spotifyUri},{
      withCredentials: true,
    })
  },
  getSearchSong: async function(query: string): Promise<Array<Song>> {
    return axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/search", {
      params: {
        q: query
      },
      withCredentials: true,
    }).then((response: AxiosResponse<Song[], any>) => response.data)
  },
  isLoggedIn: function(): boolean {
    return Cookies.get("accessToken") ? true : false;
  }
}

export default NetworkService;