import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { API_BASE_URL } from "../config";
import { loginSchema } from "../schemas/loginSchema";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const LoginCard = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [errorMsg, setErrorMsg] = useState(
    "Unable to login. please check your inputs"
  );
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(false);
    setLoading(true);

    const validation = loginSchema.safeParse(formData);
    if (!validation.success) {
      setError(true);
      setLoading(false);
      console.log("Validation errors:", validation.error.format());
      return;
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/user/login`,
        formData
      );
      const jwt = response.data.access_token;
      localStorage.setItem("token", jwt);
      setError(false);
      navigate("/");
    } catch (error) {
      console.log(error);
      console.error("Login error:", error.response.data.errors);
      setError(true);
      setErrorMsg("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="w-full max-w-xs" onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">Login to your account</CardTitle>
        </CardHeader>

        <CardContent>
          {error && <p className="text-sm text-red-500 mb-4">{errorMsg}</p>}
          <div className="flex flex-col gap-6">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="m@example.com"
                required
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
              />
            </div>
          </div>
        </CardContent>

        <CardFooter className="flex-col gap-2">
          <Button
            type="submit"
            className="w-full bg-[#32a220]"
            disabled={loading}
          >
            {loading ? "Loading..." : "Login"}
          </Button>
          <a href="#" className="py-2 pb-0 inline-block text-sm">
            Forgot your password?
          </a>
        </CardFooter>
      </Card>
    </form>
  );
};

export default LoginCard;
