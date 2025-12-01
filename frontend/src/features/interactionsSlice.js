import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../api/api";

export const postChat = createAsyncThunk(
  "interactions/postChat",
  async (text, { rejectWithValue }) => {
    try {
      const res = await api.post("/api/interactions/chat", { text });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail || "Server error");
      return json;
    } catch (err) {
      return rejectWithValue(err.message || "Network error");
    }
  }
);

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    loading: false,
    error: null,
    lastResponse: null,
    interactions: []
  },
  reducers: {
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(postChat.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(postChat.fulfilled, (state, action) => {
        state.loading = false;
        state.lastResponse = action.payload;
        if (action.payload?.interaction_id) {
          state.interactions.unshift(action.payload);
        }
      })
      .addCase(postChat.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || action.error.message;
      });
  },
});

export const { clearError } = interactionsSlice.actions;
export default interactionsSlice.reducer;
