import React from "react";

const Navbar: React.FC = () => {
  return (
    <nav className="w-full h-12 bg-gray-200 flex items-center justify-between px-4 border-b">
      <span className="font-bold">Window Name</span>
      <div className="flex gap-4">
        <span>My Profile</span>
        <button className="text-red-500">Logout</button>
      </div>
    </nav>
  );
};

const Sidebar: React.FC = () => {
  return (
    <aside className="w-1/5 h-full bg-gray-100 p-4 border-r">
      <ul className="space-y-2">
        <li className="font-bold">Projects</li>
        <li className="text-gray-700">Project Name</li>
        <li>Audio Clips</li>
        <li>Metrics</li>
        <li>Analytics</li>
      </ul>
    </aside>
  );
};

const TopContainer: React.FC = () => {
  return (
    <div className="w-full h-32 bg-white p-4 shadow-md flex justify-between">
      <div className="w-1/3 bg-gray-50 p-2 border rounded">Mean Opinion Score</div>
      <div className="w-1/3 bg-gray-50 p-2 border rounded">Total Participants</div>
      <div className="w-1/3 bg-gray-50 p-2 border rounded">Project Managers</div>
    </div>
  );
};

const Table: React.FC = () => {
  return (
    <div className="w-full bg-white p-4 shadow-md mt-4 overflow-auto">
      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-200 border-b">
            <th className="p-2 border">Audio Clips</th>
            <th className="p-2 border">Tags</th>
            <th className="p-2 border">Date Added</th>
            <th className="p-2 border">Evaluated</th>
            <th className="p-2 border">Rating</th>
          </tr>
        </thead>
        <tbody>
          {/* Placeholder data */}
          <tr className="border-b">
            <td className="p-2 border text-blue-600 cursor-pointer">Screaming.mp3</td>
            <td className="p-2 border">Fast Speech, Child</td>
            <td className="p-2 border">2/5/2025</td>
            <td className="p-2 border">48/50</td>
            <td className="p-2 border">3.6</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

const MainScreen: React.FC = () => {
  return (
    <div className="flex w-full h-screen">
      <Sidebar />
      <div className="flex-1 p-4">
        <TopContainer />
        <Table />
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <div className="flex flex-col w-full h-screen">
      <Navbar />
      <MainScreen />
    </div>
  );
};

export default App;