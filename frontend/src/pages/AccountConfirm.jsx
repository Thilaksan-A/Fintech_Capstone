import { Check } from 'lucide-react';
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function AccountConfirm() {
    const navigate = useNavigate();

    useEffect (() => {
        const timer = setTimeout(() => {
            navigate("/");
        }, 2000);
        return () => clearTimeout(timer)
    }, [navigate]);

    const investor_type = localStorage.getItem("investor");
    return(
        <div className="flex justify-center items-center h-screen flex-col">
            <p>Profile has successfully been created!</p>
            <p>Your investor type is <b>{investor_type}</b></p>
            <Check color="#32a220" />
        </div>
    )
}

export default AccountConfirm;