import { Card } from "@/components/ui/card";

interface SportCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  features: string[];
  onClick: () => void;
}

export function SportCard({ icon, title, description, features, onClick }: SportCardProps) {
  return (
    <Card 
      className="bg-card border-2 border-card-border hover:border-brand-accent transition-all duration-300 cursor-pointer shadow-card hover:shadow-brand group"
      onClick={onClick}
    >
      <div className="p-8 space-y-6">
        {/* Icon */}
        <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center">
          <div className="text-brand-accent">
            {icon}
          </div>
        </div>
        
        {/* Content */}
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-brand-accent group-hover:text-brand-accent transition-colors duration-300">
            {title}
          </h3>
          
          <p className="text-muted-foreground">
            {description}
          </p>
          
          <ul className="space-y-2">
            {features.map((feature, index) => (
              <li key={index} className="flex items-center text-sm text-muted-foreground">
                <div className="w-1.5 h-1.5 bg-brand-accent rounded-full mr-3 flex-shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}