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
        query: query
      }
    }

    ).then((response: AxiosResponse<Song[], any>) => response.data)
  }
}

export default NetworkService;