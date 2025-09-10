import { House, Newspaper, UserPen } from 'lucide-react';
import { Link } from 'react-router-dom';

function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-md z-50">
      <div className="flex justify-around items-center py-3 text-gray-600">
        <Link to="/news" className="flex flex-col items-center text-sm hover:text-blue-600">
          <Newspaper />
          <span>News</span>
        </Link>
        <Link to="/" className="flex flex-col items-center text-sm hover:text-blue-600">
          <House />
          <span>Home</span>
        </Link>
        <Link to="/profile" className="flex flex-col items-center text-sm hover:text-blue-600">
          <UserPen />
          <span>Profile</span>
        </Link>
      </div>
    </nav>
  );
}

export default BottomNav;
