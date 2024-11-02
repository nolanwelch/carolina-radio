import { Box } from "@mui/material";
import Song from "../../types/Song";
import SongDisplay from "../SongDisplay/SongDisplay";

export default function NextUp(props: { songs: Song[] }) {
  return (
    <>
      {props.songs.map((item, index) =>
        <Box sx={{marginBottom: "6px"}} key={index}>
          <SongDisplay song={item}/>
        </Box>
      )}
    </>);
}