// Welcome page for non-authenticated users

import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { ArrowRight, FileText, Grid3X3, Users, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const Index = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Navigation */}
      <nav className="border-b bg-card/50 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileText className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold text-foreground">UML Editor</span>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button className="bg-gradient-primary hover:opacity-90 shadow-elegant-sm transition-smooth">
                    <Grid3X3 className="mr-2 h-4 w-4" />
                    Go to Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="ghost" className="hover:bg-accent transition-fast">
                      Sign In
                    </Button>
                  </Link>
                  <Link to="/signup">
                    <Button className="bg-gradient-primary hover:opacity-90 shadow-elegant-sm transition-smooth">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center space-y-8 max-w-4xl">
          <div className="space-y-4">
            <h1 className="text-5xl lg:text-6xl font-bold tracking-tight text-foreground">
              Create Beautiful 
              <span className="text-transparent bg-gradient-primary bg-clip-text"> UML Diagrams</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Collaborate on UML diagrams with your team using our powerful markdown-based editor 
              with live Mermaid.js preview.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button 
                  size="lg" 
                  className="bg-gradient-primary hover:opacity-90 shadow-elegant-md transition-smooth text-lg px-8"
                >
                  <Grid3X3 className="mr-2 h-5 w-5" />
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/signup">
                  <Button 
                    size="lg" 
                    className="bg-gradient-primary hover:opacity-90 shadow-elegant-md transition-smooth text-lg px-8"
                  >
                    Start Creating
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/login">
                  <Button 
                    variant="outline" 
                    size="lg" 
                    className="border-border hover:bg-accent transition-fast text-lg px-8"
                  >
                    Sign In
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-card/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Everything you need for UML collaboration
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed for modern teams working with UML diagrams and documentation.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto shadow-elegant-md">
                <FileText className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Live Preview</h3>
              <p className="text-muted-foreground">
                See your UML diagrams render in real-time as you type with our Monaco editor and Mermaid.js integration.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto shadow-elegant-md">
                <Users className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Team Collaboration</h3>
              <p className="text-muted-foreground">
                Share and collaborate on diagrams with your team members. Organize files by teams and projects.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="h-16 w-16 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto shadow-elegant-md">
                <Zap className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Auto-save</h3>
              <p className="text-muted-foreground">
                Never lose your work with automatic saving. Focus on creating while we handle the rest.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto text-center space-y-8 max-w-2xl">
          <h2 className="text-3xl font-bold text-foreground">
            Ready to start diagramming?
          </h2>
          <p className="text-muted-foreground text-lg">
            Join thousands of teams already using UML Editor for their documentation needs.
          </p>
          {isAuthenticated ? (
            <Link to="/dashboard">
              <Button 
                size="lg" 
                className="bg-gradient-primary hover:opacity-90 shadow-elegant-md transition-smooth text-lg px-8"
              >
                <Grid3X3 className="mr-2 h-5 w-5" />
                Go to Dashboard
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          ) : (
            <Link to="/signup">
              <Button 
                size="lg" 
                className="bg-gradient-primary hover:opacity-90 shadow-elegant-md transition-smooth text-lg px-8"
              >
                Get Started for Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card/50 backdrop-blur-md py-8 px-4">
        <div className="container mx-auto text-center text-muted-foreground">
          <p>&copy; 2024 UML Editor. Built with React, TypeScript, and Mermaid.js.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
