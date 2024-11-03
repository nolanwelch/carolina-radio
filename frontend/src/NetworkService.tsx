import Cookies from "js-cookie";
import Song from "./types/Song";
import axios, { AxiosResponse } from 'axios';

const NetworkService = {
  getQueue: function() {

  },
  postSong: function(songId: string) {

  },
  getSearchSong: async function(query: string): Promise<Array<Song>> {
    return axios.get<Array<Song>>(process.env.REACT_APP_API_URL + "/search", {
      params: {
        q: query
      },
      withCredentials: true,
    }

    ).then((response: AxiosResponse<Song[], any>) => response.data)
  },
  isLoggedIn: function(): boolean {
    return Cookies.get("accessToken") ? true : false;
  }
}

export default NetworkService;