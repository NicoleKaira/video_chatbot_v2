import axios from "axios";
import {Type} from "@/model/Course";
import {Visibility} from "@/model/Visibility"; // Ensure axios is imported
const BASE_URL = process.env.NEXT_PUBLIC_SERVER_URL;

async function triggerVisibilityChange(newOption: string, type: Type, id: string) {
  try {
    const getVisibilityKey = (value: string): keyof typeof Visibility | undefined => {
      return Object.keys(Visibility).find(key => Visibility[key as keyof typeof Visibility] === value) as keyof typeof Visibility;
    }
    const res = await axios.put(BASE_URL + `/visibility`, {
      "newOption": getVisibilityKey(newOption),
      "type": type.toString(),
      "id": id
      },
    {
      headers: { 'Content-Type': 'application/json' },
    });
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw error;
    } else {
      throw new Error('different error than axios');
    }
  }
}

export default {
  triggerVisibilityChange
};
