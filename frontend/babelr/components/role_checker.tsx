import React, {useEffect, useState } from "react";

export default function RoleCheck({
  	requiredRole,
  	children,
} : {
  	requiredRole: string;
  	children: React.ReactNode;
}) {
	const [userRole, setUserRole] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);


	useEffect(() => {
		async function fetchRole() {
			try {
				const res = await fetch('http://localhost:8016/getRoleFromID', {
					method: "GET",
					credentials: "include",
				});
				const data = await res.json();
				setUserRole(data.role || null);
			} catch {
				setUserRole(null);
			} finally {
				setLoading(false);
			}
		}

    	fetchRole();
  	}, []);

  	if (loading) { 
		return (
			<div>
				Loading...
			</div>
		);
	}

	if (userRole !== requiredRole) {
		return (
		  <div>You are not authorised.</div>
		);
	  }
	  
	  return (
		<>
		  {children}
		</>
	  );
}