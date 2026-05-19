import { useEffect, useState } from 'react'
import { api, type ClassInfo, type InterfaceInfo, type FileInfo } from '@/lib/api'
import { useProject } from '@/lib/project-context'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ClassTable } from '@/components/explorer/ClassTable'
import { InterfaceTable } from '@/components/explorer/InterfaceTable'
import { NamespaceList } from '@/components/explorer/NamespaceList'
import { FileTree } from '@/components/explorer/FileTree'
import { EmptyState } from '@/components/common/EmptyState'

export function ExplorerPage() {
  const { selected } = useProject()
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [interfaces, setInterfaces] = useState<InterfaceInfo[]>([])
  const [namespaces, setNamespaces] = useState<string[]>([])
  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    if (!selected) return
    setLoading(true)
    setClasses([])
    setInterfaces([])
    setNamespaces([])
    setFiles([])
    setFetchError(null)
    Promise.all([
      api.getClasses(selected),
      api.getInterfaces(selected),
      api.getNamespaces(selected),
      api.getFiles(selected),
    ]).then(([c, i, n, f]) => {
      setClasses(c)
      setInterfaces(i)
      setNamespaces(n)
      setFiles(f)
    }).catch(err => {
      setFetchError(err instanceof Error ? err.message : 'Failed to load project data. Is the server running?')
    }).finally(() => setLoading(false))
  }, [selected])

  if (!selected) {
    return (
      <EmptyState
        heading="No project selected"
        body="Select a project from the header to explore its classes, interfaces, and files."
      />
    )
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">{selected}</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Code explorer</p>
      </div>
      {fetchError && (
        <p className="text-sm text-destructive">{fetchError}</p>
      )}
      <Tabs defaultValue="classes">
        <TabsList>
          <TabsTrigger value="classes">
            Classes {!loading && classes.length > 0 && <span className="ml-1.5 text-xs opacity-70">({classes.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="interfaces">
            Interfaces {!loading && interfaces.length > 0 && <span className="ml-1.5 text-xs opacity-70">({interfaces.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="namespaces">
            Namespaces {!loading && namespaces.length > 0 && <span className="ml-1.5 text-xs opacity-70">({namespaces.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="files">
            Files {!loading && files.length > 0 && <span className="ml-1.5 text-xs opacity-70">({files.length})</span>}
          </TabsTrigger>
        </TabsList>
        <TabsContent value="classes" className="mt-4">
          <ClassTable classes={classes} loading={loading} />
        </TabsContent>
        <TabsContent value="interfaces" className="mt-4">
          <InterfaceTable interfaces={interfaces} loading={loading} />
        </TabsContent>
        <TabsContent value="namespaces" className="mt-4">
          <NamespaceList namespaces={namespaces} loading={loading} />
        </TabsContent>
        <TabsContent value="files" className="mt-4">
          <FileTree files={files} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
