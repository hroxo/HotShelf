import axios from "./axios";

export const getShelfs = async () => {
  const [s6591, s6371, s6373] = await Promise.all([
    axios.get("/6591"),
    axios.get("/6371"),
    axios.get("/6373"),
  ]);

  const formatShelf = (shelf: any) => {
    return shelf?.data?.detections ? shelf.data : undefined;
  };

  return {
    s6591: formatShelf(s6591),
    s6371: formatShelf(s6371),
    s6373: formatShelf(s6373),
  };
};
