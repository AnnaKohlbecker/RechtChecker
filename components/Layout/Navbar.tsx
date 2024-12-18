import { FC } from "react";
import { ScaleIcon } from "@heroicons/react/24/solid"; // Heroicon for "Law/Justice"

export const Navbar: FC = () => {
  return (
    <div className="relative flex flex-col bg-white py-2 px-2 sm:px-8 items-center justify-between">
      {/* Content */}
      <div className="flex items-center space-x-2 font-bold text-3xl">
        <ScaleIcon className="h-8 w-8 text-black" />
        <p>RechtChecker</p>
      </div>
      <div className="w-full mt-2">
        <div className="h-[4px] bg-black"></div>
        <div className="h-[4px] bg-red-500"></div>
        <div className="h-[4px] bg-yellow-400"></div>
      </div>
    </div>
  );
};
