import { configureStore } from "@reduxjs/toolkit";
import interactionsReducer from "./features/interactionsSlice";

const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
  },
});

export default store;
