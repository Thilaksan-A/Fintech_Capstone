import { Link } from "react-router-dom";

import SplitText from "../components/ui/SplitText";

import LoginCard from "@/components/LoginCard";
import { Button } from "@/components/ui/button"

function Login() {
  const handleAnimationComplete = () => {
    console.log('All letters have animated!');
  };

  return (
    <div className="flex justify-center items-center h-screen flex-col">
      <div className="w-8">
        <img src="/logo.png" />
      </div>
      <SplitText
        text="Welcome to SafeGuard"
        className="text-2xl text-center pt-2 pb-4"
        delay={70}
        duration={0.3}
        ease="power3.out"
        splitType="chars"
        from={{ opacity: 0, y: 40 }}
        to={{ opacity: 1, y: 0 }}
        threshold={0.1}
        rootMargin="-100px"
        textAlign="center"
        onLetterAnimationComplete={handleAnimationComplete}
      />
      <LoginCard />
      <Link to="/signup"><Button className="p-9" variant="link">No account yet? Sign up</Button></Link>
    </div>
  )
}

export default Login;