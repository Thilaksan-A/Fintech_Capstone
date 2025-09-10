import axios from "axios";
import { useState } from "react";
import { Link } from "react-router-dom";

import { API_BASE_URL } from "../config";
import { registrationSchema } from "../schemas/registrationSchema";

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

const SignupCard = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password_hash: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [errorMsg, setErrorMsg] = useState(
    "Error creating account please check inputs."
  );

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(false);
    setLoading(true);

    const validation = registrationSchema.safeParse(formData);
    if (!validation.success) {
      setError(true);
      setLoading(false);
      console.log("Validation errors:", validation.error.format());
      return;
    }
    try {
      const response = await axios.post(`${API_BASE_URL}/api/user/`, formData);
      console.log("User created:", response.data);
      const jwt = response.data.access_token;
      localStorage.setItem("token", jwt);
      setError(false);
      onSuccess();
    } catch (error) {
      console.error(
        "Error creating user:",
        error.response?.data || error.message || error.response?.data?.errors
      );
      setLoading(false);
      setError(true);
    }
  };

  return (
    <div className="absolute z-50">
      <form role="form" className="w-full max-w-xs" onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">
              Create your account with us!
            </CardTitle>
          </CardHeader>

          <CardContent>
            {error && <p data-testid="signup-error" className="text-sm text-red-500 mb-4">{errorMsg}</p>}
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>

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
                <Label htmlFor="password_hash">Password</Label>
                <Input
                  id="password_hash"
                  name="password_hash"
                  type="password"
                  required
                  value={formData.password_hash}
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
              {loading ? "Loading..." : "Next"}
            </Button>
          </CardFooter>
        </Card>

        <Link to="/login">
          <Button className="p-9 w-full" variant="link">
            Already got an account? Log in
          </Button>
        </Link>
      </form>
    </div>
  );
};

export default SignupCard;
