import Marquee from "react-fast-marquee";

import SignupCard from "@/components/SignupCard";

function Signup({ onSuccess }) {
  return (
    <div className="relative flex justify-center items-center min-h-screen overflow-hidden">
      <Marquee
        autoFill={true}
        className="absolute text-3xl md:text-9xl font-bold uppercase top-1/2 left-1/2 min-w-screen -translate-x-1/2 -translate-y-1/2 z-0 text-center opacity-50 pointer-events-none"
      >
        {"\u00A0"}crypto made easy +
      </Marquee>
      <SignupCard onSuccess={onSuccess} />
    </div>
  );
}

export default Signup;
