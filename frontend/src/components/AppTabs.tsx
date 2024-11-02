import { Box, Tab, Tabs } from '@mui/material';
import { useState } from 'react';
import Song from '../types/Song';
import NextUp from './NextUp/NextUp';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const SAMPLE_SONGS: Song[] = [
  {
    title: "Example Song",
    artist: "Example Artist", 
    album: "Example Album",
    coverUrl: "https://narcmagazine.com/wp-content/uploads/2024/10/mxmtoon.png",
    lengthMs: 210000,
    requestCount: 15
  },
  {
    title: "Epic Song",
    artist: "Epic Artist", 
    album: "Epic Album",
    coverUrl: "/album-art-tmp.png",
    lengthMs: 210000,
    requestCount: 15
  },
  {
    title: "Temp Song",
    artist: "Temp Artist", 
    album: "Temp Album",
    coverUrl: "/album-art-tmp.png",
    lengthMs: 210000,
    requestCount: 15
  }
]

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function AppTabs() {
  const [value, setValue] = useState(0);
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };
  
  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs variant="fullWidth" value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Next Up"/>
          <Tab label="My Queue"/>
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <NextUp songs={SAMPLE_SONGS}/>
      </TabPanel>
      <TabPanel value={value} index={1}>
        Queue component here
      </TabPanel>
    </>
  );
}

export default AppTabs;