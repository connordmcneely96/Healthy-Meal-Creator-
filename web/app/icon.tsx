import { ImageResponse } from "next/server";

export const size = {
  width: 64,
  height: 64
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 36,
          background: "#2563eb",
          color: "white",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 12,
          fontWeight: 700
        }}
      >
        AI
      </div>
    ),
    {
      ...size
    }
  );
}
