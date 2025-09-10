import React from "react";

export default function LoadingOverlay() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-10 z-50">
      <div className="flex flex-col items-center space-y-4">
        <div className="w-10 h-10 border-4 border-color-custom-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-lg font-semibold text-gray-800">Loading...</p>
      </div>
    </div>
  );
}
