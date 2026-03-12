export default function DashboardGrid({
  children
}) {

  return (

    <div className="grid grid-cols-3 gap-6 mb-8">
      {children}
    </div>

  );
}