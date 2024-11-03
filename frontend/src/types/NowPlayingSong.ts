import Song from "./Song";

export default interface NowPlayingSong extends Song {
    position: number
}