import React from "react"
import { useNavigate } from "react-router-dom";

function LandingPage() {
	const navigate = useNavigate();

	const handleLogin = () => {
		navigate("/login")
	}

	const handleSignUp = () => {
		navigate("/signup")
	}

	return (
		<div className="min-h-screen bg-gray-50 relative overflow-hidden">
			{/* Gray Gradient from the Bottom */}
			<div
				className="absolute inset-0 bg-gradient-to-t from-stone-200 
					via-stone-100/70 via-stone-50/40 to-transparent 
					pointer-events-none z-0"
			>

			</div>
			{/* Header */}
			<header className="relative z-10 px-6 py-6">
				<nav className="flex items-center justify-between max-w-7xl mx-auto">
					<div className="flex items-center">
						<div className="w-8">
							<img src="/logo.png" />
						</div>
						<span className="ml-3 text-xl font-bold text-black">SafeGuard</span>
					</div>

					<div className="flex items-center space-x-4">
						<button
							onClick={handleLogin}
							className="px-4 py-2 text-black font-semibold rounded-md"
            	style={{ backgroundColor: '#b8d4d1' }}
						>
							Login
						</button>
					</div>
				</nav>
			</header>

			{/* Text */}
			<main className="relative z-10 flex flex-col items-center justify-center 
				min-h-[calc(100vh-120px)] px-6">
				<div className="text-center max-w-4xl mx-auto mb-12">
					<h1 className="text-5xl md:text-7xl font-bold text-black mb-8 
						leading-tight">
						Trade Crypto
						<br />
						<span style={{ color: '#8faa7a' }}>
              with ease
            </span>
					</h1>

					<p className="text-xl md:text-2xl text-gray-600 mb-12 leading-relaxed 
						max-w-3xl mx-auto">
						Generating actionable, scenario-based recommendations based off 
						financial data, social sentiments, and real-time coin price dynamics
					</p>
				</div>

				{/* Get Started Button */}
				<button
					onClick={handleSignUp}
					className="flex items-center px-8 py-4 text-lg font-semibold 
						text-black rounded-full"
          style={{ 
            backgroundColor: '#b8d4d1',
            border: '1px solid #b8d4d1'
          }}
				>
					Get Started
					<span className="ml-2">→</span>
				</button>

			</main>
		</div>
	)
}   

export default LandingPage;